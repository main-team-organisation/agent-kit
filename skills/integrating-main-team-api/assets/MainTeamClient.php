<?php
// MainTeamClient.php: a minimal Main Team API client (PHP 8.1+, ext-curl, firebase/php-jwt).
// Generated from the Main Team API contract 1.1.1: the minimal client of
// https://hub.main-team.org/api/clients/build-your-own. Do not edit: it is rebuilt with every release.
declare(strict_types=1);

use Firebase\JWT\JWT;

final class ApiError extends RuntimeException
{
    public function __construct(
        public readonly int $status,
        public readonly string $errorCode,
        string $message,
        public readonly ?string $requestId = null,
        public readonly ?int $retryAfter = null,
    ) {
        parent::__construct($message);
    }
}

final class MainTeamClient
{
    private const BASE_URL = 'https://api.main-team.org/v1'; // sandbox: 'https://apisnd.main-team.org/v1'
    private const TOKEN_LIFETIME = 900; // seconds; the API accepts at most 3600
    private const RENEW_BEFORE = 60;    // sign a new token this long before exp

    private ?string $token = null;
    private int $tokenExp = 0;

    public function __construct(private readonly string $apiKey, private readonly string $apiSecret)
    {
        if (!preg_match('/^key_[A-Za-z0-9_-]{24}$/', $apiKey)) {
            throw new InvalidArgumentException('apiKey is not in the issued format');
        }
        if ($apiSecret === '') {
            throw new InvalidArgumentException('apiSecret is missing');
        }
    }

    private function bearer(): string
    {
        $now = time();
        if ($this->token === null || $now >= $this->tokenExp - self::RENEW_BEFORE) {
            $this->tokenExp = $now + self::TOKEN_LIFETIME;
            $this->token = JWT::encode(
                ['sub' => $this->apiKey, 'iat' => $now, 'exp' => $this->tokenExp],
                $this->apiSecret,
                'HS256',
                $this->apiKey, // the fourth argument becomes the kid header
            );
        }
        return $this->token;
    }

    /** One request. Returns [headers, body]; throws ApiError on a 4xx or 5xx answer. */
    private function send(string $method, string $path, array $query = [], ?array $body = null, int $timeout = 30): array
    {
        $headers = [];
        $ch = curl_init(self::BASE_URL . $path . ($query ? '?' . http_build_query($query) : ''));
        $sent = ['Authorization: Bearer ' . $this->bearer(), 'X-Request-Id: ' . bin2hex(random_bytes(16))];
        if ($body !== null) {
            $sent[] = 'Content-Type: application/json';
            curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($body, JSON_THROW_ON_ERROR));
        }
        curl_setopt_array($ch, [
            CURLOPT_CUSTOMREQUEST => $method,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_CONNECTTIMEOUT => 5,
            CURLOPT_TIMEOUT => $timeout,
            CURLOPT_HTTPHEADER => $sent,
            CURLOPT_HEADERFUNCTION => static function ($ch, string $line) use (&$headers): int {
                if (str_contains($line, ':')) {
                    [$name, $value] = explode(':', $line, 2);
                    $headers[strtolower(trim($name))] = trim($value);
                }
                return strlen($line);
            },
        ]);
        $raw = curl_exec($ch); // false on a network error or a transfer cut short
        if ($raw === false) {
            throw new RuntimeException('Request failed: ' . curl_error($ch));
        }
        $status = curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
        if ($status >= 400) {
            $error = json_decode($raw, true)['error'] ?? [];
            throw new ApiError(
                $status,
                $error['code'] ?? 'unknown',
                $error['message'] ?? "HTTP $status",
                $error['request_id'] ?? $headers['x-request-id'] ?? null,
                isset($headers['retry-after']) ? (int) $headers['retry-after'] : null,
            );
        }
        return [$headers, $raw];
    }

    /** A JSON route. Returns the envelope: success, message, data and maybe pagination. */
    public function request(string $method, string $path, array $query = [], ?array $body = null): array
    {
        [, $raw] = $this->send($method, $path, $query, $body);
        $json = json_decode($raw, true, 512, JSON_THROW_ON_ERROR);
        // validate-me is the one JSON route that answers without an envelope.
        return $path === '/api-account/validate-me' ? ['success' => true, 'data' => $json] : $json;
    }

    /** Every item of a paginated list, 100 per page (the maximum). */
    public function paginate(string $path, array $query = []): Generator
    {
        for ($page = 1; ; $page++) {
            $envelope = $this->request('GET', $path, ['page' => $page, 'limit' => 100] + $query);
            foreach ($envelope['data'] as $item) {
                yield $item;
            }
            if ($page >= ($envelope['pagination']['totalPages'] ?? 0)) {
                return;
            }
        }
    }

    /** A certificate or report download. Saves the file and returns its name. */
    public function download(string $path, string $directory = '.'): string
    {
        [$headers, $raw] = $this->send('GET', $path, timeout: 120);
        if (isset($headers['content-length']) && strlen($raw) !== (int) $headers['content-length']) {
            throw new RuntimeException('Download ended early');
        }
        $disposition = $headers['content-disposition'] ?? '';
        $name = preg_match("/filename\\*=UTF-8''([^;]+)/i", $disposition, $m) ? rawurldecode($m[1])
            : (preg_match('/filename="([^"]*)"/i', $disposition, $m) ? $m[1] : 'download.pdf');
        $name = basename($name);
        file_put_contents($directory . '/' . $name, $raw);
        return $name;
    }
}
