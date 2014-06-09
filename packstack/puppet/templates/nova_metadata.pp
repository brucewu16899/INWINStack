
nova::generic_service { 'metadata-api':
    enabled        => true,
    ensure_package => 'present',
    package_name   => 'nova-api-metadata',
    service_name   => 'nova-api-metadata',
}
