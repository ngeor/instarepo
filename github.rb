require 'json'
require 'net/http'

class Github
  def get_repos
    # curl -u username:password 'https://api.github.com/user/repos'
    # if 2FA is on, password needs to replaced by personal access token
    uri = URI('https://api.github.com/user/repos')
    req = Net::HTTP::Get.new(uri)
    req.basic_auth username, password
    res = Net::HTTP.start(uri.hostname, uri.port, use_ssl: true) do |http|
      http.request(req)
    end
    JSON.parse(res.body)
  end

  def create_repo(name)
    uri = URI('https://api.github.com/user/repos')
    req = Net::HTTP::Post.new(uri)
    req.basic_auth username, password
    req.body = JSON.generate(
      name: name,
      description: 'a test repository created automatically',
      auto_init: true,
      gitignore_template: 'Maven',
      license_template: 'mit'
    )
    res = Net::HTTP.start(uri.hostname, uri.port, use_ssl: true) do |http|
      http.request(req)
    end
    JSON.parse(res.body)
  end

  def clone_url(owner, name, use_ssh = true)
    if use_ssh
      "git@github.com:#{owner}/#{name}.git"
    else
      "https://github.com/#{owner}/#{name}.git"
    end
  end

  private

  def username
    ENV['GITHUB_USERNAME']
  end

  def password
    ENV['GITHUB_PASSWORD']
  end
end
