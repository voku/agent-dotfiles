<?php

declare(strict_types=1);

namespace Arrayy\Experiment;

use function Arrayy\create;
use function PHPStan\Testing\assertType;

/** @param array<string, \DateTimeImmutable> $records */
function verifyTypedFactory(array $records): void
{
    $result = create($records);
    assertType('DateTimeImmutable|null', $result->first());
}
