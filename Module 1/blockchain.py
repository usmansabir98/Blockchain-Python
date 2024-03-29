# -*- coding: utf-8 -*-
"""
Module 1 - Create a Blockchain

Created on Thu Sep 12 15:16:16 2019

@author: Usman Sabir
"""

import datetime
import hashlib
import json
from flask import Flask, jsonify

class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.create_block(proof=1, previous_hash='0')
        
    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain)+1,
            'timestamp': str(datetime.datetime.now()),
            "proof": proof,
            "previous_hash": previous_hash
        }
        
        self.chain.append(block)
        return block;
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, prev_proof):
        new_proof = 1
        check_proof = False
        
        while check_proof is False:
            problem = new_proof**2 - prev_proof**2
            hash_operation = hashlib.sha256(str(problem).encode()).hexdigest()
            if hash_operation[:4]=='0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        prev_block = chain[0]
        index = 1
        
        while index < len(chain):
            block = chain[index]
            if block["previous_hash"]!=self.hash(prev_block):
                return False
            
            prev_proof = prev_block["proof"]
            proof = block["proof"]
            
            problem = proof**2 - prev_proof**2
            hash_operation = hashlib.sha256(str(problem).encode()).hexdigest()
            
            if hash_operation[:4]!='0000':
                return False
            
            prev_block = block
            index +=1
            
        return True

# part 2
        
app = Flask(__name__)

blockchain = Blockchain()

@app.route('/mine_block', methods=["GET"])
def mine_block():
    prev_block = blockchain.get_previous_block()
    proof = blockchain.proof_of_work(prev_block["proof"])
    
    prev_hash = blockchain.hash(prev_block)
    block = blockchain.create_block(proof, prev_hash)
    
    response = {"message": "You just mined a block", 
                'index': block["index"],
                'timestamp': block["timestamp"],
                "proof": block["proof"],
                "previous_hash": block["previous_hash"]
                }
    
    return jsonify(response), 200


@app.route('/get_chain', methods=["GET"])
def get_chain():
    response = {"chain": blockchain.chain,
                "length": len(blockchain.chain)}
    
    return jsonify(response), 200


@app.route('/is_valid', methods=["GET"])
def is_valid():
    valid = blockchain.is_chain_valid(blockchain.chain)
    response = {"valid": valid}
    
    return jsonify(response), 200

app.run(host = '0.0.0.0', port= 5000)    