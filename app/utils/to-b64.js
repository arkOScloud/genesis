export default function toB64(data) {
    return window.btoa(data).replace(/\=/g, '*').replace(/\//g, '-');
}
