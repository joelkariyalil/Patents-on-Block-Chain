const hre = require("hardhat");

async function main() {
  const PatentVerifier = await hre.ethers.getContractFactory("PatentVerifier");
  const contract = await PatentVerifier.deploy();
  await contract.waitForDeployment();
  const address = await contract.getAddress();  // ✅ properly await
  console.log("✅ Contract deployed to:", address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
