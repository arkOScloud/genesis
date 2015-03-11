Genesis.Router.map(function () {
  this.resource('domains', function(){
    this.resource('domain', { path: '/:domain_id' }, function(){
      this.route('edit');
    });
  });
  this.resource('groups', function(){
    this.resource('group', { path: '/:group_id' }, function(){
      this.route('edit');
    });
  });
  this.resource('users', function(){
    this.resource('user', { path: '/:user_id' }, function(){
      this.route('edit');
    });
  });
  this.resource('certs', function(){
    this.resource('cert', { path: '/:cert_id' }, function(){
      this.route('info');
    });
  });
  this.resource('databases', function(){
    this.resource('database', { path: '/:database_id' }, function(){
      this.route('edit');
    });
  });
  this.resource('filesystems', function(){
    this.resource('filesystem', { path: '/:filesystem_id' }, function(){
      this.route('edit');
    });
  });
  this.resource('websites', function(){
    this.resource('website', { path: '/:website_id' }, function(){
      this.route('edit');
    });
  });
  this.resource('packages', function(){
    this.resource('package', { path: '/:package_id' }, function(){
      this.route('edit');
    });
  });
  this.resource('apps', function(){
    this.resource('app', { path: '/:app_id' }, function(){
      this.route('edit');
    });
  });
  this.route('stats');
  this.route('services');
  this.route('fileman');
  this.route('config');
});
