// Script to update Mac power settings for sleep/wake scheduling
const { execSync } = require('child_process');

try {
  console.log('Setting up sleep/wake scheduling for M4 Mac Mini...');
  
  // Set the computer to sleep at 11 PM
  execSync('pmset -a sleep 60', { stdio: 'inherit' }); // Sleep after 60 mins of inactivity
  execSync('pmset -a displaysleep 15', { stdio: 'inherit' }); // Display sleep after 15 mins
  
  // Schedule a wake event for 7 AM (only works from sleep, not from shutdown)
  execSync('pmset schedule wake "07:00:00"', { stdio: 'inherit' });
  
  console.log('Power settings updated successfully');
} catch (error) {
  console.error('Error updating power settings:', error.message);
}