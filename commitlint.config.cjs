module.exports = {
  extends: ["@commitlint/config-conventional"],
  rules: {
    "type-enum": [
      2,
      "always",
      [
        "feat",
        "fix",
        "docs",
        "refactor",
        "test",
        "chore",
        "ci",
        "perf",
        "setting",
        "deploy"
      ]
    ],
    "subject-case": [0],
    "body-empty": [2, "never"]
  }
};
