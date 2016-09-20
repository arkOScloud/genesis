import Ember from 'ember';
import cardColor from '../utils/card-color';


export function generateCardColor() {
  return cardColor();
}

export default Ember.Helper.helper(generateCardColor);
