require "active_support/core_ext/integer/time"

Rails.application.configure do
  config.enable_reloading = false
  config.eager_load = true
  config.consider_all_requests_local = false
  
  config.force_ssl = true
  config.assume_ssl = true

  config.active_support.deprecation = :notify
  config.log_tags = [:request_id]
  config.log_level = ENV.fetch("RAILS_LOG_LEVEL", "info")

  config.active_record.dump_schema_after_migration = false
end
