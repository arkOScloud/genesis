import Ember from 'ember';
import config from './config/environment';

const Router = Ember.Router.extend({
  location: config.locationType
});

Router.map(function() {
  this.route('app', { path: '/app' }, function() {
    this.route('radicale', function() {
      this.route('new-book');
      this.route('new-cldr');
    });
    this.route('syncthing', function() {
      this.route('settings');
      this.route('folders', function() {
        this.route('edit', { path: '/:folder_id' });
        this.route('add');
      });
      this.route('devices', function() {
        this.route('edit', { path: '/:device_id' });
        this.route('add');
      });
    });
    this.route('xmpp');
  });
  this.route('apps', { path: '/apps' }, function() {
    this.route('info', { path: '/:app_id' });
  });
  this.route('websites', function(){
    this.route('edit', { path: '/:website_id' });
    this.route('add');
  });

  this.route('system', function() {
    this.route('backups', function(){
      this.route('info', { path: '/:backup_id' });
    });
    this.route('config');
    this.route('networks', function() {
      this.route('info', { path: '/:network_id' });
      this.route('add');
    });
    this.route('packages', function(){
      this.route('info', { path: '/:package_id' });
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
    this.route('services');
    this.route('updates');
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
    this.route('files', function() {});
    this.route('filesystems', function(){
      this.route('info', { path: '/:filesystem_id' });
      this.route('add');
    });
    this.route('stats');
    this.route('shares', function() {
      this.route('shares', function() {
        this.route('info', { path: '/:share_id' });
        this.route('add');
      });
      this.route('mounts', function() {
        this.route('add');
      });
    });
  });

  this.route('firstrun');
  this.route('login');
});

export default Router;
