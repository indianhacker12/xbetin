// DOM Elements
const walletDisplay = document.getElementById('wallet-balance');
const grid = document.getElementById('grid');
const slotsContainer = document.querySelector('.slots-container');
const rowsInput = document.getElementById('rows');
const updateRowsButton = document.getElementById('update-rows');
const betButton = document.getElementById('bet-button');
const betAmountInput = document.getElementById('bet-amount');

// Game Variables
let walletBalance = 1000;
let rows = parseInt(rowsInput.value);
const slotMultipliers = [5, 3, 2, 1, 0.5, 1, 0.5, 1, 2, 3, 5];

// Create Plinko Grid
function createGrid(rows) {
  grid.innerHTML = '';
  for (let i = 0; i < rows; i++) {
    const row = document.createElement('div');
    row.classList.add('row');
    for (let j = 0; j <= i; j++) {
      const peg = document.createElement('div');
      peg.classList.add('peg');
      row.appendChild(peg);
    }
    grid.appendChild(row);
  }
}

// Create Slots
function createSlots() {
  slotsContainer.innerHTML = '';
  slotMultipliers.forEach((multiplier, index) => {
    const slot = document.createElement('div');
    slot.classList.add('slot');
    slot.textContent = `${multiplier}x`;
    slot.dataset.multiplier = multiplier;
    slotsContainer.appendChild(slot);
  });
}

// Drop Ball Simulation
function dropBall(betAmount) {
  const ball = document.createElement('div');
  ball.classList.add('ball');
  ball.style.left = `${grid.offsetWidth / 2}px`;
  grid.appendChild(ball);

  let currentRow = 0;
  const interval = setInterval(() => {
    if (currentRow < rows) {
      const pegsInRow = grid.children[currentRow].children;
      const randomPeg = pegsInRow[Math.floor(Math.random() * pegsInRow.length)];
      ball.style.top = `${randomPeg.offsetTop + 20}px`;
      ball.style.left = `${randomPeg.offsetLeft + 20}px`;
      currentRow++;
    } else {
      clearInterval(interval);
      const randomSlot = slotsContainer.children[Math.floor(Math.random() * slotMultipliers.length)];
      const multiplier = parseFloat(randomSlot.dataset.multiplier);
      const winnings = betAmount * multiplier;

      if (multiplier > 1) {
        walletBalance += winnings;
        alert(`You win ₹${winnings}!`);
      } else {
        walletBalance -= betAmount;
        alert('You lose!');
      }

      walletDisplay.textContent = walletBalance;
      ball.remove();
    }
  }, 200);
}

// Event Listeners
updateRowsButton.addEventListener('click', () => {
  rows = parseInt(rowsInput.value);
  if (rows < 8 || rows > 16) {
    alert('Rows must be between 8 and 16!');
    return;
  }
  createGrid(rows);
});

betButton.addEventListener('click', () => {
  const betAmount = parseInt(betAmountInput.value);
  if (isNaN(betAmount) || betAmount <= 0 || betAmount > walletBalance) {
    alert('Invalid bet amount!');
    return;
  }
  dropBall(betAmount);
});

// Initialize Game
createGrid(rows);
createSlots();
