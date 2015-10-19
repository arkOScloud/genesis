export default function sizeToString(sz) {
    if (sz < 1024) {
      return sz+' bytes';
    }
    sz = sz / 1024.0;
    if (sz < 1024) {
      return sz.toFixed(2)+' Kb';
    }
    sz = sz / 1024.0;
    if (sz < 1024) {
      return sz.toFixed(2)+' Mb';
    }
    sz = sz / 1024.0;
    if (sz < 1024) {
      return sz.toFixed(2)+' Gb';
    }
    sz = sz / 1024.0;
    return sz.toFixed(2)+' Tb';
}
