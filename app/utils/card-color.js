/* global moment */

var cardColors = ["card-image red", "card-image green", "card-image blue",
  "card-image orange", "card-image teal", "card-image olive", "card-image violet"];

export default function cardColor() {
  var len = cardColors.length;
  if (moment().month() === 11) {
    len = 2;
  }
  var index = Math.floor(Math.random() * len);
  return cardColors[index];
}
