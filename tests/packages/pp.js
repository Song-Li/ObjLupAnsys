function foo(key1, key2, value) {
  var target = {};
  var proto = target[key1];
  proto[key2] = value;
}
function input_value(val) {
  var mid = val + " ";
  return mid;
}

function pp(key1, key2, value) {
  tmp = input_value(value);
  foo(key1, key2, tmp);
}

module.exports = {pp: pp}
