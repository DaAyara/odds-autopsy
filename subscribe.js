const anchor = require("@coral-xyz/anchor");
const { Connection, PublicKey, SystemProgram, Keypair } = require("@solana/web3.js");
const { ASSOCIATED_TOKEN_PROGRAM_ID, TOKEN_2022_PROGRAM_ID, getAssociatedTokenAddressSync, createAssociatedTokenAccountIdempotentInstruction } = require("@solana/spl-token");
const { Transaction } = require("@solana/web3.js");
const axios = require("axios");
const nacl = require("tweetnacl");
const fs = require("fs");

const keypairData = JSON.parse(fs.readFileSync("wallet.json", "utf8"));
const keypair = Keypair.fromSecretKey(Uint8Array.from(keypairData));

const API_ORIGIN = "https://txline.txodds.com";
const RPC_URL = "https://api.mainnet-beta.solana.com";
const PROGRAM_ID = new PublicKey("9ExbZjAapQww1vfcisDmrngPinHTEfpjYRWMunJgcKaA");
const TXL_MINT = new PublicKey("Zhw9TVKp68a1QrftncMSd6ELXKDtpVMNuMGr1jNwdeL");

const SERVICE_LEVEL_ID = 12;
const DURATION_WEEKS = 4;
const SELECTED_LEAGUES = [];

async function main() {
  const connection = new Connection(RPC_URL, "confirmed");
  const wallet = new anchor.Wallet(keypair);
  const provider = new anchor.AnchorProvider(connection, wallet, { commitment: "confirmed" });
  anchor.setProvider(provider);

  const idl = JSON.parse(fs.readFileSync("idl/txoracle.json", "utf8"));
  const program = new anchor.Program(idl, provider);

  const userTokenAccountCheck = getAssociatedTokenAddressSync(
    TXL_MINT, keypair.publicKey, false, TOKEN_2022_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID
  );

  const createAtaIx = createAssociatedTokenAccountIdempotentInstruction(
    keypair.publicKey,
    userTokenAccountCheck,
    keypair.publicKey,
    TXL_MINT,
    TOKEN_2022_PROGRAM_ID,
    ASSOCIATED_TOKEN_PROGRAM_ID
  );

  const ataTx = new Transaction().add(createAtaIx);
  const ataSig = await provider.sendAndConfirm(ataTx);
  console.log("Token account ready:", ataSig);

  console.log("Wallet:", keypair.publicKey.toBase58());
  console.log("Subscribing to service level", SERVICE_LEVEL_ID, "for", DURATION_WEEKS, "weeks...");

  const [tokenTreasuryPda] = PublicKey.findProgramAddressSync(
    [Buffer.from("token_treasury_v2")],
    PROGRAM_ID
  );

  const tokenTreasuryVault = getAssociatedTokenAddressSync(
    TXL_MINT, tokenTreasuryPda, true, TOKEN_2022_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID
  );

  const [pricingMatrixPda] = PublicKey.findProgramAddressSync(
    [Buffer.from("pricing_matrix")],
    PROGRAM_ID
  );

  const userTokenAccount = getAssociatedTokenAddressSync(
    TXL_MINT, keypair.publicKey, false, TOKEN_2022_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID
  );

  const txSig = await program.methods
    .subscribe(SERVICE_LEVEL_ID, DURATION_WEEKS)
    .accounts({
      user: keypair.publicKey,
      pricingMatrix: pricingMatrixPda,
      tokenMint: TXL_MINT,
      userTokenAccount,
      tokenTreasuryVault,
      tokenTreasuryPda,
      tokenProgram: TOKEN_2022_PROGRAM_ID,
      associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
      systemProgram: SystemProgram.programId,
    })
    .rpc();

  console.log("Subscription tx:", txSig);

  const authResponse = await axios.post(`${API_ORIGIN}/auth/guest/start`);
  const jwt = authResponse.data.token;

  const messageString = `${txSig}::${jwt}`;
  const message = new TextEncoder().encode(messageString);
  const signatureBytes = nacl.sign.detached(message, keypair.secretKey);
  const walletSignature = Buffer.from(signatureBytes).toString("base64");

  const activationResponse = await axios.post(
    `${API_ORIGIN}/api/token/activate`,
    { txSig, walletSignature, leagues: SELECTED_LEAGUES },
    { headers: { Authorization: `Bearer ${jwt}` } }
  );

  const apiToken = activationResponse.data.token || activationResponse.data;

  fs.appendFileSync(".env", `\nTXLINE_JWT=${jwt}\nTXLINE_API_TOKEN=${apiToken}\n`);
  console.log("Done. API token saved to .env");
}

main().catch(console.error);