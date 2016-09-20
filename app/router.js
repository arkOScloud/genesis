import Ember from 'ember';
import config from './config/environment';

const Router = Ember.Router.extend({
  location: config.locationType
});

Router.map(function() {
  this.route('domains', function(){
    this.route('domain', { path: '/:domain_id' }, function(){
      this.route('edit');
    });
  });
  this.route('groups', function(){
    this.route('group', { path: '/:group_id' }, function(){
      this.route('edit');
    });
  });
  this.route('users', function(){
    this.route('user', { path: '/:user_id' }, function(){
      this.route('edit');
    });
  });
  this.route('certs', function(){
    this.route('cert', { path: '/:cert_id' }, function(){
      this.route('info');
    });
  });
  this.route('databases', function(){
    this.route('database', { path: '/:database_id' }, function(){
      this.route('edit');
    });
  });
  this.route('filesystems', function(){
    this.route('filesystem', { path: '/:filesystem_id' }, function(){
      this.route('edit');
    });
  });
  this.route('websites', function(){
    this.route('website', { path: '/:website_id' }, function(){
      this.route('edit');
    });
  });
  this.route('packages', function(){
    this.route('package', { path: '/:package_id' }, function(){
      this.route('edit');
    });
  });
  this.route('apps', { path: '/apps' }, function() {
    this.route('info', { path: '/:app_id' });
  });
  this.route('backups', function(){
    this.route('backup', { path: '/:backup_id' }, function(){
      this.route('edit');
    });
  });
  this.route('networks', function(){
    this.route('network', { path: '/:network_id' }, function(){
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
  this.route('roles', function() {
    this.route('users', function() {
      this.route('edit', { path: '/:user_id' });
      this.route('add');
    });
    this.route('groups', function() {
      this.route('edit', { path: '/:group_id' });
      this.route('add');
    });
    this.route('domains', function() {
      this.route('add');
    });
  });
});

export default Router;
