export default function handleModelError(self, e) {
  if (e.responseJSON) {
    e = e.responseJSON;
  }
  if (e.errors && e.errors.report) {
    self.transitionToRoute("error", e.errors);
    return;
  } else if (e.errors) {
    self.notifications.new('error', e.errors[0].detail);
  }
}
