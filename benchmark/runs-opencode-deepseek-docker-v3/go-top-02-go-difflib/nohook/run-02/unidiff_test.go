package unidiff

import "testing"

func TestUnifiedContext(t *testing.T) {
	tests := []struct {
		name    string
		a, b    string
		context int
		want    string
	}{
		{
			name:    "identical",
			a:       "one\ntwo\n",
			b:       "one\ntwo\n",
			context: 3,
			want:    "",
		},
		{
			name:    "single change",
			a:       "one\ntwo\nthree\n",
			b:       "one\nTWO\nthree\n",
			context: 3,
			want: "--- a\n+++ b\n" +
				"@@ -1,3 +1,3 @@\n" +
				" one\n" +
				"-two\n" +
				"+TWO\n" +
				" three\n",
		},
		{
			name:    "insertion",
			a:       "one\nthree\n",
			b:       "one\ntwo\nthree\n",
			context: 3,
			want: "--- a\n+++ b\n" +
				"@@ -1,2 +1,3 @@\n" +
				" one\n" +
				"+two\n" +
				" three\n",
		},
		{
			name:    "deletion",
			a:       "one\ntwo\nthree\n",
			b:       "one\nthree\n",
			context: 3,
			want: "--- a\n+++ b\n" +
				"@@ -1,3 +1,2 @@\n" +
				" one\n" +
				"-two\n" +
				" three\n",
		},
		{
			name:    "zero context",
			a:       "one\ntwo\nthree\n",
			b:       "one\nTWO\nthree\n",
			context: 0,
			want: "--- a\n+++ b\n" +
				"@@ -2 +2 @@\n" +
				"-two\n" +
				"+TWO\n",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := UnifiedContext(tt.a, tt.b, tt.context); got != tt.want {
				t.Errorf("UnifiedContext() =\n%q\nwant\n%q", got, tt.want)
			}
		})
	}
}

func TestUnifiedSeparateHunks(t *testing.T) {
	a := "a\nb\nc\nd\ne\nf\ng\nh\ni\n"
	b := "A\nb\nc\nd\ne\nf\ng\nh\nI\n"

	got := Unified(a, b)
	want := "--- a\n+++ b\n" +
		"@@ -1,4 +1,4 @@\n" +
		"-a\n" +
		"+A\n" +
		" b\n" +
		" c\n" +
		" d\n" +
		"@@ -6,4 +6,4 @@\n" +
		" f\n" +
		" g\n" +
		" h\n" +
		"-i\n" +
		"+I\n"

	if got != want {
		t.Errorf("Unified() =\n%q\nwant\n%q", got, want)
	}
}

func TestUnifiedAdditionAtEnd(t *testing.T) {
	got := Unified("a\n", "a\nb\n")
	want := "--- a\n+++ b\n" +
		"@@ -1 +1,2 @@\n" +
		" a\n" +
		"+b\n"
	if got != want {
		t.Errorf("Unified() =\n%q\nwant\n%q", got, want)
	}
}
