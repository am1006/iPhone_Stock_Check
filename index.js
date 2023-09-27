import fetch from "node-fetch";

const botToken = process.env.botToken;
const chatID = process.env.chatID;

async function checkAvailability() {
  const url =
    "https://www.apple.com/au/shop/fulfillment-messages?pl=true&mts.0=regular&mts.1=compact&parts.0=MU783ZP/A&searchNearby=true&store=R483";
  const headers = {
    "Content-Type": "application/json",
    "User-Agent":
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
  };
  const body = {};

  const response = await fetch(url, {
    method: "POST",
    headers,
    body,
  });

  const results = await response.json();

  //   console.log(results);

  const canberraStore = results.body.content.pickupMessage.stores[0];

  if (!canberraStore || canberraStore.storeName !== "Canberra") {
    console.log("Canberra store not found");
    return;
  }

  const partsAvailability = canberraStore.partsAvailability["MU783ZP/A"];
  const pickupDisplay = partsAvailability.pickupDisplay;

  const storePickupProductTitle =
    partsAvailability.messageTypes.compact.storePickupProductTitle;
  const storePickupQuote =
    partsAvailability.messageTypes.compact.storePickupQuote;

  return [pickupDisplay, storePickupProductTitle, storePickupQuote];
}

// Telegram
function teleMsg(msg) {
  const telegram =
    "https://api.telegram.org/bot" +
    botToken +
    "/sendMessage?chat_id=" +
    chatID +
    "parse_mode=HTML&text=";

  (async () => {
    try {
      await fetch(telegram + msg, {
        method: "POST",
      });
    } catch (error) {
      console.log(error.response.body);
    }
  })();
}

async function scheduled() {
  const [pickupDisplay, storePickupProductTitle, storePickupQuote] =
    await checkAvailability();

  if (!pickupDisplay || !storePickupProductTitle || !storePickupQuote) {
    console.log("Canberra store not found");
    return;
  }

  if (pickupDisplay !== "available") {
    let message = `Not available: ${storePickupProductTitle} - ${storePickupQuote}`;
    console.log(message);

    // try {
    //   console.log("Starting TeleMsg...");
    //   teleMsg(encodeURI(message));
    //   console.log("Not available message sent");
    // } catch (error) {
    //   console.log("Here is the error with TeleMsg:");
    //   console.log(error);
    // }
    return;

  } else {
    let message = `${storePickupProductTitle} - ${storePickupQuote}`;
    console.log(message);

    try {
      console.log("Starting TeleMsg...");
      teleMsg(encodeURI(message));
      console.log("Available message sent");
    } catch (error) {
      console.log("Here is the error with TeleMsg:");
      console.log(error);
    }
  }
}

scheduled();
