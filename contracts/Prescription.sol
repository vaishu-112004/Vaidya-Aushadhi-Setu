// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Prescription {

    struct Data {
        uint id;
        string ipfsHash;
        address doctor;
        address patient;
    }

    mapping(uint => Data) public prescriptions;

    uint public count;

    function addPrescription(string memory ipfsHash,address patient) public {

        count++;

        prescriptions[count] = Data(
            count,
            ipfsHash,
            msg.sender,
            patient
        );
    }
}