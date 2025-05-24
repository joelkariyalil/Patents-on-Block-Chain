// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract PatentVerifier {
    struct Record {
        string cid;
        uint256 score;
        string decision;
        uint256 timestamp;
    }

    mapping(address => Record[]) public userRecords;

    event RecordStored(address indexed user, string cid, uint256 score, string decision, uint256 timestamp);

    function storeResult(string memory _cid, uint256 _score, string memory _decision) public {
        Record memory newRecord = Record(_cid, _score, _decision, block.timestamp);
        userRecords[msg.sender].push(newRecord);

        emit RecordStored(msg.sender, _cid, _score, _decision, block.timestamp);
    }

    function getUserRecords(address user) public view returns (Record[] memory) {
        return userRecords[user];
    }
}
