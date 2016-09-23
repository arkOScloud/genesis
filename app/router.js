import Ember from 'ember';
import config from './config/environment';

const Router = Ember.Router.extend({
  location: config.locationType
});

Router.map(function() {
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
  this.route('updates');

  this.route('settings', function() {
    this.route('config');
    this.route('networks', function() {
      this.route('info', { path: '/:network_id' });
      this.route('add');
    });
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
    this.route('security', function() {
      this.route('firewall', function() {
        this.route('add');
      });
      this.route('fail2ban');
    });
  });
  this.route('tools', function() {
    this.route('certificates', function(){
      this.route('info', { path: '/:certificate_id' });
      this.route('add');
    });
    this.route('databases', function(){
      this.route('add');
      this.route('add-user');
      this.route('info', { path: '/:database_id' });
      this.route('user-edit', { path: '/user/:database-user_id' });
    });
    this.route('files');
    this.route('filesystems', function(){
      this.route('info', { path: '/:filesystem_id' });
      this.route('add');
    });
    this.route('services');
    this.route('stats');
  });

  this.route('firstrun');
  this.route('login');
});

export default Router;
