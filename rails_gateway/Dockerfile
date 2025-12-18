FROM ruby:3.2.2

# Install dependencies
RUN apt-get update -qq && apt-get install -y build-essential libpq-dev nodejs

WORKDIR /rails

# Install Gems
COPY Gemfile Gemfile.lock ./
RUN bundle install

# Copy application code
COPY . .

# Expose port 3000
EXPOSE 3000

# Start server
CMD ["rails", "server", "-b", "0.0.0.0"]