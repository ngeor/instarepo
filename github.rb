require 'json'
require 'net/http'
require_relative './repo_provider_base'
require_relative './rest_client'

# GitHub repository provider.
class GitHub < RepoProviderBase
  def repos
    # curl -u username:password 'https://api.github.com/user/repos'
    # if 2FA is on, password needs to replaced by personal access token
    url = 'https://api.github.com/user/repos'

    rest_client.get(url, basic_auth: basic_auth)
  end

  def repo_exists?
    url = 'https://api.github.com/repos/' \
    "#{repo_options.owner}/#{repo_options.name}"

    begin
      rest_client.get(url, basic_auth: basic_auth)
    rescue RestClientError => e
      raise e unless e.code.to_s == '404'
      false
    else
      true
    end
  end

  def create_repo
    url = 'https://api.github.com/user/repos'
    body = {
      name: repo_options.name,
      description: repo_options.description,
      auto_init: true,
      gitignore_template: 'Maven',
      license_template: 'mit'
    }
    rest_client.post(url, body, basic_auth: basic_auth)
  end

  def clone_url(use_ssh = true)
    if use_ssh
      "git@github.com:#{repo_options.owner}/#{repo_options.name}.git"
    else
      "https://github.com/#{repo_options.owner}/#{repo_options.name}.git"
    end
  end
end
