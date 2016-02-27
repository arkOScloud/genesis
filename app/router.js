import Ember from 'ember';
import config from './config/environment';

const Router = Ember.Router.extend({
  location: config.locationType
});

Router.map(function() {
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
  this.resource('backups', function(){
    this.resource('backup', { path: '/:backup_id' }, function(){
      this.route('edit');
    });
  });
  this.resource('networks', function(){
    this.resource('network', { path: '/:network_id' }, function(){
      this.route('edit');
    });
  });
  this.route('stats');
  this.route('services');
  this.route('security');
  this.route('config');
  this.route('updates');
  this.route('files');
  this.route('firstrun');
  this.route('login');
});

export default Router;
