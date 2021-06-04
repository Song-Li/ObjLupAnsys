var test = require('tape');
var deep = require('./');

test('deep gets', function (t) {
  var obj = {
    foo: 'bar',
    bar: {
      baz: {
        beep: 'boop'
      }
    }
  };

  t.equal(deep(obj, 'foo'), 'bar');
  t.equal(deep(obj, 'bar.baz.beep'), 'boop');
  t.equal(deep(obj, 'bar.baz.beep.yep.nope'), undefined);
  t.end();
});

test('deep gets with array of paths', function (t) {
  var obj = {
    foo: 'bar',
    bar: {
      baz: {
        beep: 'boop'
      },
      'baz.beep': 'blop'
    }
  };

  t.equal(deep(obj, ['bar', 'baz', 'beep']), 'boop');
  t.equal(deep(obj, ['bar', 'baz', 'beep', 'yep', 'nope']), undefined);
  t.equal(deep(obj, ['bar', 'baz.beep']), 'blop');
  t.end();
})

test('deep sets', function (t) {
  var obj = {
    foo: 'bar',
    bar: {
      baz: {
        beep: 'boop'
      }
    }
  };

  function p () {
    deep(obj, 'yep.nope', 'p');
  }

  t.equal(deep(obj, 'foo', 'yep'), 'yep');
  t.equal(obj.foo, 'yep');
  t.equal(deep(obj, 'bar.baz.beep', 'nope'), 'nope');
  t.equal(obj.bar.baz.beep, 'nope');
  t.throws(p);

  deep.p = true;

  t.equal(deep(obj, 'yep.nope', 'p'), 'p');
  t.equal(obj.yep.nope, 'p');

  t.end();
});

test('deep sets with array of paths', function (t) {
  var obj = {
    foo: 'bar',
    bar: {
      baz: {
        beep: 'boop'
      }
    }
  };

  t.equal(deep(obj, 'foo', 'yep'), 'yep');
  t.equal(obj.foo, 'yep');
  t.equal(deep(obj, ['bar', 'baz', 'beep'], 'nope'), 'nope');
  t.equal(obj.bar.baz.beep, 'nope');
  t.equal(deep(obj, ['bar', 'baz.beep'], 'nooope'), 'nooope');
  t.equal(obj.bar['baz.beep'], 'nooope');
  t.end();
});

test('deep deletes', function (t) {
  var obj = {
    foo: 'bar',
    bar: {
      baz: {
        beep: 'boop'
      }
    }
  };

  t.equal(deep(obj, 'foo', undefined), undefined);
  t.notOk(obj.foo);
  t.equal(deep(obj, 'bar.baz', undefined), undefined);
  t.notOk(obj.bar.baz);
  t.equal(deep(obj, 'bar.baz.beep'), undefined);
  t.end();
});

test('do not get `__proto__`, `prototype` or `constructor` properties', function (t) {
  var obj = {
    isAdmin: false,
    __proto__: {
      isAdmin: true
    },
    prototype: {
      isAdmin: true
    },
    constructor: {
      isAdmin: true,
      prototype: {
        isAdmin: true
      }
    }
  };

  t.equal(deep(obj, 'isAdmin'), false);
  t.equal(deep(obj, '__proto__.isAdmin'), undefined);
  t.equal(deep(obj, 'prototype.isAdmin'), undefined);
  t.equal(deep(obj, 'constructor.isAdmin'), undefined);
  t.equal(deep(obj, 'constructor.prototype.isAdmin'), undefined);
  t.end();
});

test('do not set `__proto__`, `prototype` or `constructor` properties', function (t) {
  var obj = {};

  deep.p = true;

  deep(obj, 'isAdmin', false);
  deep(obj, '__proto__.isAdmin', true);
  deep(obj, 'prototype.isAdmin', true);
  deep(obj, 'constructor.isAdmin', true);
  deep(obj, 'constructor.prototype.isAdmin', true);

  t.equal(obj.isAdmin, false);
  t.equal(obj.__proto__ && obj.__proto__.isAdmin, undefined);
  t.equal(obj.prototype && obj.prototype.isAdmin, undefined);
  t.equal(obj.constructor && obj.constructor.isAdmin, undefined);
  t.equal(
    obj.constructor &&
    obj.constructor.prototype &&
    obj.constructor.prototype.isAdmin,
    undefined
  );
  t.end();
});
