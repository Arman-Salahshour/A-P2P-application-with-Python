# A P2P Matrix Multiplication Application

[A P2P application.pdf](https://github.com/Arman-Salahshour/A-P2P-application-with-Python/files/6913360/A.P2P.application.pdf)

## Overview
This project implements a Peer-to-Peer (P2P) network for multiplying large matrices using Python. The architecture is built around a centralized P2P model, where a main server coordinates the peers' interactions and ensures efficient resource management. The solution leverages the Strassen algorithm for matrix multiplication and addresses challenges like network congestion and resource limitations.

---

## Features
- **Centralized P2P Network**: A main server manages the peers by storing their information (IP, port, and usage status) and facilitates peer-to-peer communication.
- **Dynamic Peer Management**: Peers can request connections to seven other peers for matrix multiplication tasks.
- **Matrix Multiplication Using Strassen's Algorithm**: Efficiently multiplies matrices by dividing the computation across peers.
- **Concurrency Handling**: Manages simultaneous connections and ensures robust operation through thread-based architecture.

---

## Architecture
### Centralized P2P Model
- **Main Server**: Maintains a table (using pandas DataFrame) to track peer information and manage requests.
  - Registers new peers.
  - Assigns seven unused peers to a requesting peer.
  - Releases peers after use.
  - Handles network congestion using semaphore locks and a round-robin approach.

- **Peers**: Each peer functions both as a client and a server.
  - Can request a list of seven peers for tasks.
  - Hosts connections to other peers for distributed computations.
  - Executes tasks like creating matrices, multiplying matrices, and releasing resources.

---

## Key Functionalities
### Main Server
- **Registration**: Adds peers to the table with their IP, port, and usage status.
- **Request Handling**: Allocates seven peers for computation if resources are available.
- **Peer Release**: Frees up peers after they complete their tasks.
- **Network Congestion Management**: Handles resource contention using semaphores and a first-come-first-served strategy.

### Peer
- **Server Side**: Listens for incoming requests and handles distributed matrix computation.
- **Client Side**: Connects to assigned peers and collaborates on computational tasks.
- **Strassen Algorithm**: Divides large matrices into smaller submatrices, distributes computations, and combines results.

---

## Usage Instructions
### Prerequisites
- Python 3.6 or later.
- Required Python libraries: `numpy`, `pandas`, `pickle`.

### Running the Application
1. **Start the Main Server**:
   ```bash
   python main-server.py
   ```
   The server starts listening on the default IP and port defined in `constants.py`.

2. **Initialize a Peer**:
   ```bash
   python peer.py
   ```
   Each peer connects to the main server and initializes its server and client functionalities.

3. **Execute Commands on a Peer**:
   - Request peers: `I need seven peers`
   - Release peers: `release these peers`
   - Create matrices: `make matrices`
   - Multiply matrices: `multiply matrices`

### Example
- The `multiply matrices` command uses the Strassen algorithm to divide and distribute matrix multiplication tasks across peers. Results are computed collaboratively and aggregated.

---

## Technical Details
### Files
- `constants.py`: Contains shared constants and semaphore definitions.
- `main-server.py`: Implements the main server, peer registration, and resource management.
- `peer.py`: Defines peer behaviors, including client and server operations.
- `strassen.py`: Provides the implementation of the Strassen matrix multiplication algorithm.

### Strassen Algorithm
The Strassen algorithm divides matrices into smaller blocks and recursively computes products, reducing the computational complexity compared to standard methods. This implementation supports distributed computation by delegating submatrix multiplications to different peers.

---

## Challenges and Solutions
### Network Congestion
- **Problem**: Limited resources can cause peers to wait indefinitely.
- **Solution**: Round-robin scheduling and semaphore locks ensure fair and efficient resource allocation.

### Peer Failure
- **Problem**: Peers may disconnect unexpectedly.
- **Solution**: The main server detects and removes inactive peers, ensuring system stability.

---

## License
This project is open-source and available under the MIT License.




