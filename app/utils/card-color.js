var cardColors = ["card-image red", "card-image blue", "card-image orange",
  "card-image green", "card-image teal", "card-image olive", "card-image violet"];

export default function cardColor() {
  var index = Math.floor(Math.random() * cardColors.length);
  return cardColors[index];
}
