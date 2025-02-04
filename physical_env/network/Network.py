import copy
import numpy as np
class Network:
    def __init__(self, env, listNodes, baseStation, listTargets):
        self.env = env
        self.listNodes = listNodes
        self.baseStation = baseStation
        self.listTargets = listTargets
        self.targets_active = [1 for _ in range(len(self.listTargets))]

        # Setting BS and Node environment and network
        baseStation.env = self.env
        baseStation.net = self

        self.frame = np.array([self.baseStation.location[0], self.baseStation.location[0], self.baseStation.location[1], self.baseStation.location[1]])
        it = 0
        for node in self.listNodes:
            node.env = self.env
            node.net = self
            node.id = it
            it += 1
            self.frame[0] = min(self.frame[0], node.location[0])
            self.frame[1] = max(self.frame[1], node.location[0])
            self.frame[2] = min(self.frame[2], node.location[1])
            self.frame[3] = max(self.frame[3], node.location[1])

        it = 0

        # Setting name for each target
        for target in listTargets:
            target.id = it
            it += 1
         

    # Function is for setting nodes' level and setting all targets as covered
    def setLevels(self):
        for node in self.listNodes:
            node.level = -1
        tmp1 = []
        tmp2 = []
        for node in self.baseStation.direct_nodes:
            if node.status == 1:
                node.level = 1
                tmp1.append(node)

        for i in range(len(self.targets_active)):
            self.targets_active[i] = 0

        while True:
            if len(tmp1) == 0:
                break
            # For each node, we set value of target covered by this node as 1
            # For each node, if we have not yet reached its neighbor, then level of neighbors equal this node + 1
            for node in tmp1:
                for target in node.listTargets:
                    self.targets_active[target.id] = 1
                for neighbor in node.neighbors:
                    if neighbor.status == 1 and neighbor.level == -1:
                        tmp2.append(neighbor)
                        neighbor.level = node.level + 1

            # Once all nodes at current level have been expanded, move to the new list of next level
            tmp1 = tmp2[:]
            tmp2.clear()
        return


    def operate(self, t=1, max_time=1000000):
        
        for node in self.listNodes:
            self.env.process(node.operate(t=t))
        self.env.process(self.baseStation.operate(t=t))
        timeout = max_time
        while True:
            yield self.env.timeout(t / 10.0)
            timeout -= t/10.0
            self.setLevels()
            alive = self.check_targets()
            yield self.env.timeout(9.0 * t / 10.0)
            timeout -= 9.0 * t / 10.0
            tmp = 0
            for node in self.listNodes:
                if node.status == 0:
                    tmp += 1
            if self.env.now % 100 == 0:
                print(self.env.now, tmp)
            if alive == 0 or timeout < 0:
                break            
        return

    # If any target dies, value is set to 0
    def check_targets(self):
        return min(self.targets_active)
