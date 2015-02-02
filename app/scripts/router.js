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
  this.route('appstore');
  this.route('fileman');
});
