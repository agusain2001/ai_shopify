class ApplicationController < ActionController::API
  # Skip CSRF for API-only mode
  # All controllers inherit from this base class
end
