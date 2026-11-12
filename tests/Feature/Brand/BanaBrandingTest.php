<?php

declare(strict_types=1);

use App\Models\MenuItem;
use App\Services\SettingsService;
use Database\Seeders\MenuSeeder;
use Database\Seeders\SettingsSeeder;

it('uses the Bana Bot name and never seeds links to another operator', function () {
    $this->seed(SettingsSeeder::class);
    $this->seed(MenuSeeder::class);

    $settings = app(SettingsService::class);
    $welcome = (array) $settings->get('welcome.message');

    expect($welcome['en'])->toContain('Bana Bot')
        ->and($settings->get('webapp.url'))->toBeNull()
        ->and(MenuItem::query()->whereNotNull('url')->count())->toBe(0)
        ->and(MenuItem::query()->whereHas('translations', fn ($q) => $q->where('label', 'ℹ️ About Bana Bot'))->exists())->toBeTrue();
});

it('ships the distinct teal Bana Bot theme', function () {
    expect(file_exists(public_path('css/bana-theme.css')))->toBeTrue()
        ->and(file_get_contents(public_path('css/bana-theme.css')))->toContain('#008F91')
        ->and(file_exists(public_path('bana-mark.svg')))->toBeTrue()
        ->and(file_exists(public_path('css/bana-identity.css')))->toBeTrue();
});
