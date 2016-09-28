export function initialize(container, application) {
  application.inject('component', 'notifications', 'service:notifications');
  application.inject('controller', 'notifications', 'service:notifications');
  application.inject('route', 'notifications', 'service:notifications');
}

export default {
  name: 'notifications',
  initialize
};
