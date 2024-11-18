// script.js

let playerBalance = 100;
let winStreak = 0;
let lossStreak = 0;
let rollHistory = [];
let currentBetType = 'number'; // Default bet type is number

const rollButton = document.getElementById("roll-dice");
const balanceElement = document.getElementById("balance");
const betAmountElement = document.getElementById("bet-amount");
const betNumberElement = document.getElementById("bet-number");
const dice1Element = document.getElementById("dice-1");
const dice2Element = document.getElementById("dice-2");
const resultElement = document.getElementById("dice-result");
const outcomeElement = document.getElementById("outcome");
const historyListElement = document.getElementById("history-list");
const winStreakElement = document.getElementById("win-streak");
const lossStreakElement = document.getElementById("loss-streak");

const betNumberBtn = document.getElementById("bet-number-btn");
const betOddBtn = document.getElementById("bet-odd-btn");
const betEvenBtn = document.getElementById("bet-even-btn");
const betHighBtn = document.getElementById("bet-high-btn");
const betLowBtn = document.getElementById("bet-low-btn");

// Assign bet types to buttons
betNumberBtn.addEventListener("click", () => currentBetType = 'number');
betOddBtn.addEventListener("click", () => currentBetType = 'odd');
betEvenBtn.addEventListener("click", () => currentBetType = 'even');
betHighBtn.addEventListener("click", () => currentBetType = 'high');
betLowBtn.addEventListener("click", () => currentBetType = 'low');

rollButton.addEventListener("click", rollDice);

function rollDice() {
  const betAmount = parseInt(betAmountElement.value);
  const betNumber = parseInt(betNumberElement.value);

  if (isNaN(betAmount) || isNaN(betNumber) || betAmount <= 0 || betNumber < 2 || betNumber > 12) {
    alert("Please place a valid bet.");
    return;
  }

  if (betAmount > playerBalance) {
    alert("You don't have enough balance.");
    return;
  }

  // Roll two dice
  const dice1 = Math.floor(Math.random() * 6) + 1;
  const dice2 = Math.floor(Math.random() * 6) + 1;
  const diceSum = dice1 + dice2;

  // Show dice animation (simulate rolling)
  animateDice(dice1Element, dice2Element);

  // Wait for animation to finish before showing result
  setTimeout(() => {
    // Display dice results
    dice1Element.textContent = dice1;
    dice2Element.textContent = dice2;
    
    // Show total sum of dice
    resultElement.textContent = diceSum;

    // Determine if the player wins
    const isWin = checkWin(betNumber, currentBetType, diceSum, dice1, dice2);

    // Update player balance
    playerBalance = isWin ? playerBalance + betAmount * getPayout(currentBetType) : playerBalance - betAmount;
    balanceElement.textContent = playerBalance;

    // Update streaks
    if (isWin) {
      winStreak++;
      lossStreak = 0;
    } else {
      lossStreak++;
      winStreak = 0;
    }

    // Display win/loss message
    outcomeElement.textContent = isWin ? "You Win!" : "You Lose!";
    winStreakElement.textContent = winStreak;
    lossStreakElement.textContent = lossStreak;

    // Update history
    updateHistory(diceSum, betNumber, isWin);

  }, 1500);  // Wait 1.5 seconds for dice to roll

}

function checkWin(betNumber, betType, diceSum, dice1, dice2) {
  switch (betType) {
    case 'number':
      return diceSum === betNumber;
    case 'odd':
      return diceSum % 2 !== 0;
    case 'even':
      return diceSum % 2 === 0;
    case 'high':
      return diceSum >= 7;
    case 'low':
      return diceSum <= 6;
    default:
      return false;
  }
}

function getPayout(betType) {
  switch (betType) {
    case 'number':
      return 10;  // 10x payout for number bet
    case 'odd':
    case 'even':
      return 2;   // 2x payout for odd/even bet
    case 'high':
    case 'low':
      return 2;   // 2x payout for high/low bet
    default:
      return 1;
  }
}

function animateDice(dice1, dice2) {
  dice1.style.transform = "rotate(360deg)";
  dice2.style.transform = "rotate(360deg)";
}

function updateHistory(diceSum, betNumber, isWin) {
  const historyItem = document.createElement("li");
  historyItem.textContent = `Bet on: ${betNumber}, Rolled: ${diceSum}, Result: ${isWin ? "Win" : "Lose"}`;
  historyListElement.insertBefore(historyItem, historyListElement.firstChild);

  // Keep history to the last 5 rolls
  if (historyListElement.children.length > 5) {
    historyListElement.removeChild(historyListElement.lastChild);
  }
}
