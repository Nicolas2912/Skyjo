# Skyjo Reinforcement Learning Implementation 

Important note: This project is still in work and does not contain the optimal RL implementation. It may also have some bugs in regards to the game mechanics!

An advanced implementation of a reinforcement learning agent for the card game Skyjo using PPO (Proximal Policy Optimization) with action masking and sophisticated state representation.

## Technical Overview

This project implements a complete Skyjo game environment with multiple agent types, focusing on a reinforcement learning approach using the PPO algorithm. The implementation features a custom OpenAI Gym environment, action masking for valid move enforcement, and detailed state representation.

## Architecture

### Game Environment (`environment.py`)
- Core game logic implementation
- Manages game state transitions
- Handles player actions and card operations
- Implements state tracking and validation

### RL Environment (`RLEnvironment` class)
The RL environment extends OpenAI Gym and implements:

#### State Space
- Field representation: 12x18 one-hot encoded matrix
  - Encodes card values (-2 to 12)
  - Special symbols (♦ for stars)
  - Hidden/visible card states
- Last action encoding: 5-dimensional one-hot vector
Total observation space: `Box(low=0, high=1, shape=(12 * 18 + 5,), dtype=float32)`

#### Action Space
- 16 discrete actions combining:
  - Card positions (0-11)
  - Game actions (pull, discard, change)
- Action masking ensures only valid moves

#### Reward Structure
Multiple reward components:
1. Point-based rewards
```python
if current_points[self.rl_name] < self.points_in_running[-2]:
    reward += 1
if current_points[self.rl_name] < min(self.points_in_running):
    reward += 2
```
2. Normalized score rewards
```python
reward += (1 - self.theoretical_normalize(current_points[self.rl_name])) * 2
```
3. Line completion rewards
- Additional rewards for completing rows/columns
- Matching card combinations

### Agent Types

#### 1. RL Agent (`rl_agent.py`)
- Implements PPO with action masking
- Uses neural network policy
- Maintains game state history

#### 2. Simple Reflex Agent (`simple_reflex_agent.py`)
- Rule-based decision making
- Card value thresholds
- Position-based strategies

#### 3. Random Agent
- Baseline implementation
- Random action selection
- Used for comparison

### Game Components

#### Card Deck (`carddeck.py`)
- Manages card distribution
- Card value mappings
- Special card handling (stars)

#### Game Field (`gamefield.py`)
- Grid-based card layout
- Line completion detection
- Score calculation

## Implementation Details

### State Representation
The state is represented as a combination of:
```python
self.observation_space = gym.spaces.Box(
    low=0, 
    high=1, 
    shape=(12 * 18 + 5,), 
    dtype=np.float32
)
```

### Action Masking
Implemented using `MaskablePPO` from Stable-Baselines3:
```python
def action_masks(self):
    legal_actions = self._legal_actions()
    action_mask = [False] * 16
    # Mask based on game state
    if self.game_state == "running":
        if last_action == "pull deck":
            action_mask[12:14] = [True, True]
    return np.array(action_mask, dtype=bool)
```

### Training Configuration
```python
model = MaskablePPO(
    "MlpPolicy", 
    rl_env, 
    verbose=1, 
    device='cuda', 
    learning_rate=0.0001
)
model.learn(
    total_timesteps=100000, 
    progress_bar=True, 
    callback=logging_callback
)
```

### Performance Monitoring
- Episode rewards tracking
- Wrong action counting
- Performance visualization
- Learning curves

## Installation and Setup

1. Clone the repository
2. Install dependencies:
```bash
pip install torch gymnasium stable-baselines3 numpy matplotlib
```

## Usage Example

```python
# Initialize environment
carddeck = Carddeck()
agent = RLAgent("RLBOT", carddeck, (4, 3))
gamefield = GameField(4, 3, [agent], carddeck)
env = Environment(gamefield)
rl_env = RLEnvironment(env)

# Training with monitoring
logging_callback = LoggingCallback()
model = MaskablePPO("MlpPolicy", rl_env, verbose=1, device='cuda')
model.learn(total_timesteps=100000, callback=logging_callback)

# Visualize results
plt.plot(rl_env.points, "-o", label="Points of agent")
plt.title("Points over time")
plt.grid()
plt.show()
```

## Key Features

### 1. Sophisticated State Management
- Complete game state tracking
- Efficient state updates
- Memory-optimized representations

### 2. Action Validation
- Comprehensive move validation
- Legal action enforcement
- Game rule compliance

### 3. Reward Engineering
- Multi-component reward system
- Progress-based incentives
- Strategic play encouragement

### 4. Performance Optimization
- GPU acceleration support
- Efficient state representations
- Optimized action masking

## Future Developments

1. Advanced Features
- Multi-agent training capabilities
- Self-play implementation
- Advanced reward shaping

2. Optimizations
- Enhanced state representation
- Improved action space efficiency
- Advanced policy architectures

## Contributing

Contributions are welcome! Please refer to the contribution guidelines for more information.

## License

MIT License - see LICENSE file for details
