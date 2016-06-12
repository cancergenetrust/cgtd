contract VarStore {
    function() { throw; }

    event VarLog(
        address _from,
        bytes variantDesc
    );

    function saveVar(bytes _varDesc) {
            VarLog(msg.sender, _varDesc);
    }
}
