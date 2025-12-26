require_relative "boot"

require "rails"
require "active_model/railtie"
require "active_record/railtie"
require "action_controller/railtie"
require "action_view/railtie"

Bundler.require(*Rails.groups)

module RailsGateway
  class Application < Rails::Application
    config.load_defaults 7.1
    
    # API-only mode
    config.api_only = true
    
    # Auto-load lib directory
    config.autoload_lib(ignore: %w[assets tasks])
    
    # Default timezone
    config.time_zone = "UTC"
  end
end
