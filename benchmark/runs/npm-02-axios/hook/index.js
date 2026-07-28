const axios = require('axios');

async function main() {
  const response = await axios.get('https://api.github.com');
  console.log(response.status, response.data);
}

main().catch((err) => {
  console.error(err.message);
  process.exit(1);
});
