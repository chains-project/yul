const axios = require('axios');

async function main() {
  const response = await axios.get('https://api.github.com');
  console.log(response.data);
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
