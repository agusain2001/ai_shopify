Rails.application.routes.draw do
  # Health check
  get "up" => "rails/health#show", as: :rails_health_check

  namespace :api do
    namespace :v1 do
      # Main Analytics Endpoint
      post 'questions', to: 'questions#create'
      
      # Shopify OAuth Routes
      get 'auth/shopify/install', to: 'auth#install'
      get 'auth/shopify/callback', to: 'auth#callback'
    end
  end
end
