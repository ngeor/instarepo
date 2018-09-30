# frozen_string_literal: true

require_relative '../repo_providers/factory'
require_relative '../file_system'
require_relative '../git'

module Commands
  # Initializes an existing repository.
  class InitCommand
    def initialize(options)
      @options = options
      dry_run = options[:dry_run] == true
      @provider = RepoProviders.create(options)
      @git = GitFactory.create(dry_run: dry_run)
      @file_system = FileSystemFactory.create(dry_run: dry_run)
    end

    def run
      if @provider.repo_exist?
        clone_or_pull
        add_readme
        true
      else
        puts 'Repo does not exist'
        false
      end
    end

    private

    def clone_or_pull
      @git.clone_url = @provider.clone_url
      @git.repo_name = @options[:name]
      @git.clone_dir = @options[:clone_dir]
      @git.clone_or_pull
    end

    def add_readme
      readme_file = File.join(@git.working_dir, 'README.md')
      if @file_system.file?(readme_file)
        puts 'Readme already exists, skipping'
      else
        do_add_readme readme_file
      end
    end

    def do_add_readme(readme_file)
      puts 'Creating new readme file'
      contents = <<~HERE
        # #{@options[:name]}
        #{@options[:description]}
      HERE
      @file_system.write(readme_file, contents)
      @git.add 'README.md'
      @git.commit 'Added README'
      @git.push
    end
  end
end