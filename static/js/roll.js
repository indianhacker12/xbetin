// roll.js

let playerBalance = 100;
let currentBet = { type: '', amount: 10 }; // Default bet amount is $10

// Betting Logic
document.getElementById('bet-red').addEventListener('click', () => {
  currentBet.type = 'red';
  alert('You have bet on Red');
});

document.getElementById('bet-black').addEventListener('click', () => {
  currentBet.type = 'black';
  alert('You have bet on Black');
});

// Spin the wheel
document.getElementById('spin-button').addEventListener('click', () => {
  if (currentBet.type === '') {
    alert('Please place a bet first!');
    return;
  }

  // Add the spinning animation to the wheel
  const wheelImage = document.getElementById('wheel-image');
  const ball = document.getElementById('roulette-ball');

  // Start the spin animation for the wheel
  wheelImage.style.animation = 'spin-wheel 4s ease-out forwards';
  
  // Reset ball position
  ball.style.transition = 'transform 4s ease-out';

  // Simulate the roulette spin and get a result
  setTimeout(() => {
    // Simulate the result
    const result = spinRouletteWheel();
    const winner = checkBetOutcome(result);

    // Set the ball position based on the result
    const angle = calculateBallPosition(result.number);
    ball.style.transform = `rotate(${angle}deg) translateX(90px)`;  // Move the ball

    // Update balance and game result
    if (winner) {
      playerBalance += currentBet.amount;
      document.getElementById('outcome').innerText = 'You Win!';
    } else {
      playerBalance -= currentBet.amount;
      document.getElementById('outcome').innerText = 'You Lose!';
    }

    // Update the game UI
    document.getElementById('balance').innerText = playerBalance;
    document.getElementById('wheel-result').innerText = result.number;
  }, 4000); // Wait for animation to complete
});

// Spin Logic (European Wheel - 37 slots)
function spinRouletteWheel() {
  const slots = [
    { number: '0', color: 'green' },
    { number: '32', color: 'red' },
    { number: '15', color: 'black' },
    { number: '19', color: 'red' },
    { number: '4', color: 'black' },
    { number: '21', color: 'red' },
    { number: '2', color: 'black' },
    { number: '25', color: 'red' },
    { number: '17', color: 'black' },
    { number: '34', color: 'red' },
    { number: '6', color: 'black' },
    { number: '27', color: 'red' },
    { number: '13', color: 'black' },
    { number: '36', color: 'red' },
    { number: '11', color: 'black' },
    { number: '30', color: 'red' },
    { number: '8', color: 'black' },
    { number: '23', color: 'red' },
    { number: '10', color: 'black' },
    { number: '5', color: 'red' },
    { number: '24', color: 'black' },
    { number: '16', color: 'red' },
    { number: '33', color: 'black' },
    { number: '1', color: 'red' },
    { number: '20', color: 'black' },
    { number: '14', color: 'red' },
    { number: '31', color: 'black' },
    { number: '9', color: 'red' },
    { number: '22', color: 'black' },
    { number: '18', color: 'red' },
    { number: '29', color: 'black' },
    { number: '7', color: 'red' },
    { number: '28', color: 'black' },
    { number: '12', color: 'red' },
    { number: '35', color: 'black' },
  ];

  // Randomly select a winning slot
  const winningSlot = slots[Math.floor(Math.random() * slots.length)];
  return winningSlot;
}

// Ball Position Calculation
function calculateBallPosition(number) {
  const slotAngles = {
    '0': 0, '32': 9.73, '15': 19.46, '19': 29.19, '4': 38.92, '21': 48.65, '2': 58.38, '25': 68.11, '17': 77.84,
    '34': 87.57, '6': 97.30, '27': 107.03, '13': 116.76, '36': 126.49, '11': 136.22, '30': 145.95, '8': 155.68,
    '23': 165.41, '10': 175.14, '5': 184.87, '24': 194.60, '16': 204.33, '33': 214.06, '1': 223.79, '20': 233.52,
    '14': 243.25, '31': 253.00, '9': 262.73, '22': 272.46, '18': 282.19, '29': 291.92, '7': 301.65, '28': 311.38,
    '12': 321.11, '35': 330.84
  };

  return slotAngles[number];
}

function checkBetOutcome(result) {
  const betColor = currentBet.type;
  if (betColor === 'red' && (result.color === 'red')) {
    return true; // Player wins
  } else if (betColor === 'black' && (result.color === 'black')) {
    return true; // Player wins
  }
  return false; // Player loses
}
