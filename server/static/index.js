const d = (ms) => {
  let debounceTimer = null;
  return (f) => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(f, ms);
  };
};

const debounce = d(1000);

const avatar = document.getElementById('avatar');
const input = document.getElementById('input');

input.addEventListener('input', () => {
  debounce(() => {
    avatar.src = "/static/img/loading.webp";
    avatar.src = `/avatar/${CryptoJS.MD5(input.value).toString()}`;
  });
});