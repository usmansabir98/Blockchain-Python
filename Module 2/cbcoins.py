# -*- coding: utf-8 -*-
"""
Module 2: Create a Cryptocurrency

Created on Sun Sep 15 21:18:04 2019

@author: Usman Sabir
"""


import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof=1, previous_hash='0')
        self.nodes = set()
        
    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain)+1,
            'timestamp': str(datetime.datetime.now()),
            "proof": proof,
            "previous_hash": previous_hash,
            "transactions": self.transactions
        }
        
        self.transactions = []
        
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
    
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({"sender": sender, "receiver": receiver, "amount": amount})
        prev_block = self.get_previous_block()
        return prev_block["index"]+1
    
    
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        
        
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
                    
        if longest_chain:
            self.chain = longest_chain
            return True
        
        return False
            

# part 2
        
app = Flask(__name__)


# creating address for node on port 5000
address = str(uuid4()).replace("-", "")

blockchain = Blockchain()

@app.route('/mine_block', methods=["GET"])
def mine_block():
    prev_block = blockchain.get_previous_block()
    proof = blockchain.proof_of_work(prev_block["proof"])
    
    prev_hash = blockchain.hash(prev_block)
    
    blockchain.add_transaction(sender=address, receiver="usman", amount=1)
    
    block = blockchain.create_block(proof, prev_hash)
    
    response = {"message": "You just mined a block", 
                'index': block["index"],
                'timestamp': block["timestamp"],
                "proof": block["proof"],
                "previous_hash": block["previous_hash"],
                "transactions": block["transactions"]
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


@app.route('/add_transaction', methods=["POST"])
def add_transaction():
    json = request.get_json()
    transaction_keys = ["sender", "receiver", "amount"]
     
    if not all (key in json for key in transaction_keys):
        return "Some elements missing", 400 
     
    index = blockchain.add_transaction(json["sender"], json["receiver"], json["amount"])
    response = {"message": f'This txn will be added to block {index}'}
    
    return jsonify(response), 201
    
app.run(host = '0.0.0.0', port= 5000)













    