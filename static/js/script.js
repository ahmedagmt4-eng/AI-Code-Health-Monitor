const loadExample = document.getElementById('loadExample');
const code = document.getElementById('code');
if (loadExample && code) {
  loadExample.addEventListener('click', () => {
    code.focus();
    code.select();
  });
}
