import { moduleFor, test } from 'ember-qunit';

moduleFor('route:app/radicale/new-book', 'Unit | Route | app/radicale/new book', {
  // Specify the other units that are required for this test.
  // needs: ['controller:foo']
});

test('it exists', function(assert) {
  let route = this.subject();
  assert.ok(route);
});
