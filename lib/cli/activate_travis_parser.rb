# frozen_string_literal: true

require 'optparse'
require_relative './common_options'

module CLI
  # Parser for the activate travis repo sub-command,
  # which activates an existing repo in Travis.
  class ActivateTravisParser
    def initialize
      # collect options here
      @options = {}
    end

    def help
      'Activates a repository in Travis, allowing it to run builds'
    end

    def parse(argv)
      option_parser = OptionParser.new do |opts|
        opts.banner = <<~HERE
          Usage: main.rb [global options] activate-travis [options]
        HERE
        define_options(opts)
      end

      option_parser.order!(argv)
      check_missing_options
      @options
    end

    private

    include CommonOptionsMixin

    def define_options(opts)
      name_option(opts)
      owner_option(opts)
      token_option(opts)
    end

    def check_missing_options
      mandatory = %i[name owner token]
      missing = mandatory.select { |p| @options[p].nil? }
      raise OptionParser::MissingArgument, missing.join(', ') \
        unless missing.empty?
    end
  end
end
