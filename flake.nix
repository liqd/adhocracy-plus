{
  description = "Development shell for adhocracy-plus";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs =  with pkgs; [
          libpqxx
          nodejs
          python3
          python3Packages.pip
          python3Packages.python-magic
          sqlite
          redis
        ];
      };
    };
}