// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ExamPaperManager {
    
    struct Paper {
        uint256 id;
        string subject;
        string ipfsHash;
        address teacher;
        address superintendent;
        bool isFinalized;
        uint256 unlockTime; // Stores Unix Timestamp
    }

    mapping(uint256 => Paper) public papers;
    uint256 public paperCount = 0;

    /**
     * @dev Finalizes the exam paper and assigns a superintendent and unlock time.
     */
    function finalizePaper(
        uint256 _id, 
        address _superintendent, 
        uint256 _unlockTime
    ) public {
        require(_id > 0 && _id <= paperCount, "Invalid ID");
        
        Paper storage p = papers[_id];
        p.superintendent = _superintendent;
        p.unlockTime = _unlockTime;
        p.isFinalized = true;
    }
}