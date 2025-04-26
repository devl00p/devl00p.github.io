FROM ruby:3.2

# Installer quelques dépendances système pour Nokogiri, etc.
RUN apt-get update && apt-get install -y build-essential libpq-dev nodejs

# Installer Bundler
RUN gem install bundler

# Installer Jekyll
RUN gem install jekyll

# Dockerfile
RUN git config --global --add safe.directory /srv/jekyll

WORKDIR /srv/jekyll

CMD ["bash"]

# Une fois lancé, `bundle exec jekyll build` pour build
# `bundle exec jekyll serve --host 0.0.0.0 pour le serveur
# `cd _site && python3 -m http.server 4000` pour skip la génération
